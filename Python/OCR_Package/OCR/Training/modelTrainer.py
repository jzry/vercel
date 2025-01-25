import torch
import torchvision
import torchvision.transforms as transforms
from datasets import load_dataset
from torch.utils.data import DataLoader
import pandas as pd
from pathlib import Path

from OCR.OkraClassifier import OkraClassifier


#############################
###### Hyperparameters ######

batch_size = 500    # If this is too big, your GPU will run out of memory
epochs = 20

lr = 0.0025
weight_decay = 5e-3

# SGD only
momentum = 0.9
nesterov = True

#############################
########## Options ##########

use_extended_MNIST = True
use_Adam_optimizer = False
load_existing_weights = False
input_weights_filename = 'okra_input.resnet.weights'
output_final_weights_filename = 'okra_final.resnet.weights'
output_best_weights_filename = 'okra_best.resnet.weights'


# Transformations to be applied to the training images
train_transform = transforms.Compose([
    transforms.RandomRotation(5),
    transforms.ToTensor()
])

# Transformations to be applied to the testing images
test_transform = transforms.Compose([
    transforms.ToTensor()
])

#############################
#############################


CUDA_VISIBLE_DEVICES=1

# By default use the CPU
device = torch.device('cpu')

# Check for GPU
if torch.cuda.is_available():
    device = torch.device('cuda')
    # print('Using device:', torch.cuda.get_device_name(device))

else:
    print('Warning: No CUDA device available')


# Disable Debugging APIs (for better performance)
torch.autograd.set_detect_anomaly(mode=False)
torch.autograd.profiler.emit_nvtx(enabled=False)
torch.autograd.profiler.profile(enabled=False)


def main():

    # Get data
    train_data, test_data = prepare_data()

    # Get model
    model = prepare_model()

    # Get optimizer
    optimizer = prepare_optimizer(model)

    # Get loss function
    criterion = torch.nn.CrossEntropyLoss()

    # Run the training
    results = train_model(model, train_data, test_data, optimizer, criterion)

    # Save the final model
    torch.save(model.state_dict(), output_final_weights_filename)

    # Save the results
    results.to_csv('training results.csv')


def apply_train_transforms(examples):

    examples['image'] = [train_transform(image) for image in examples['image']]
    return examples


def apply_test_transforms(examples):

    examples['image'] = [test_transform(image) for image in examples['image']]
    return examples


def prepare_data():

    if use_extended_MNIST:

        emnist = load_dataset('ernestchu/emnist-digits')
        train = emnist['train']
        test = emnist['test']
        train.set_transform(apply_train_transforms, columns=['image', 'label'])
        test.set_transform(apply_test_transforms, columns=['image', 'label'])

    else:

        train = torchvision.datasets.MNIST('./data', train=True, download=True, transform=train_transform)
        test = torchvision.datasets.MNIST('./data', train=False, download=True, transform=test_transform)

    train_loader = DataLoader(train, shuffle=True, batch_size=batch_size, num_workers=15)
    test_loader = DataLoader(test, shuffle=False, batch_size=batch_size, num_workers=15)

    return train_loader, test_loader


def prepare_model():

    model = OkraClassifier()
    model.to(device)

    if load_existing_weights:

        state_dict = torch.load(
            Path(__file__).parent / input_weights_filename,
            weights_only=True,
            map_location=torch.device(device)
        )
        model.load_state_dict(state_dict)

    return model


def prepare_optimizer(model):

    if use_Adam_optimizer:

        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=lr,
            weight_decay=weight_decay
        )

    else:

        optimizer = torch.optim.SGD(
            model.parameters(),
            lr=lr,
            momentum=momentum,
            nesterov=nesterov,
            weight_decay=weight_decay
        )

    return optimizer


def train_model(model, train_data, test_data, optimizer, criterion):

    results = pd.DataFrame(
        columns=['Testing Loss', 'Testing Accuracy', 'Training Loss', 'Training Accuracy']
    )

    best_accuracy = 0.0

    # Epoch 0 - Testing only
    #
    test_accuracy, test_loss = test(model, test_data, criterion)
    print(f'\nTesting:  accuracy = {test_accuracy:>0.2f}% | loss = {test_loss:.8f}')
    results.loc[0] = [test_loss, test_accuracy, '', '']

    try:
        for epoch in range(1, epochs + 1):

            print('\n------------ Epoch', epoch, '-----------')

            train_accuracy, train_loss = train_one_epoch(model, train_data, optimizer, criterion)
            print(f'Training: accuracy = {train_accuracy:>0.2f}% | loss = {train_loss:.8f}')

            test_accuracy, test_loss = test(model, test_data, criterion)
            print(f'Testing:  accuracy = {test_accuracy:>0.2f}% | loss = {test_loss:.8f}')

            # Save results
            results.loc[epoch] = [test_loss, test_accuracy, train_loss, train_accuracy]

            if epoch > 1 and test_accuracy > best_accuracy:
                best_accuracy = test_accuracy
                torch.save(model.state_dict(), output_best_weights_filename)

    except KeyboardInterrupt:
        print('KeyboardInterrupt: Saving results...')

    return results


def train_one_epoch(model, data, optimizer, criterion):

    # Set model to train mode
    model.train()

    total_correct = 0
    total_loss = 0

    for batch in data:
        if use_extended_MNIST:
            x_batch = batch['image']
            y_batch = batch['label']

        else:
            x_batch, y_batch = batch

        # Erase old gradients by setting them to None
        optimizer.zero_grad(set_to_none=True)

        # Send data to GPU
        x_batch = x_batch.to(device)
        y_batch = y_batch.to(device)

        # Inference
        pred = model(x_batch)

        # Calculate loss and update model parameters
        loss = criterion(pred, y_batch)
        loss.backward()
        optimizer.step()

        # Track statistics
        correct_pred = torch.argmax(pred, 1) == y_batch
        total_correct += correct_pred.float().sum().item()
        total_loss += loss.item()

    # Divide the loss from each batch by the number of batches
    avg_loss = total_loss / len(data)

    # Divide the number of correct predictions by the number of images
    accuracy = 100.0 * total_correct / len(data.dataset)

    return accuracy, avg_loss


def test(model, data, criterion):

    # Set model to test mode
    model.eval()

    total_correct = 0
    total_loss = 0

    with torch.no_grad():
        for batch in data:
            if use_extended_MNIST:
                x_batch = batch['image']
                y_batch = batch['label']

            else:
                x_batch, y_batch = batch

            # Send data to GPU
            x_batch = x_batch.to(device)
            y_batch = y_batch.to(device)

            # Inference
            pred = model(x_batch)

            # Compute loss for this batch
            total_loss += criterion(pred, y_batch).item()

            # Compute the number of correct predictions
            correct_pred = torch.argmax(pred, 1) == y_batch
            total_correct += correct_pred.float().sum().item()

    # Divide the loss from each batch by the number of batches
    avg_loss = total_loss / len(data)

    # Divide the number of correct predictions by the number of images
    accuracy = 100.0 * total_correct / len(data.dataset)

    return accuracy, avg_loss


if __name__=='__main__':
    main()

