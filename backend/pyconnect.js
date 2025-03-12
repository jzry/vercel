const { spawn } = require('child_process');


// The command to run Python
const pythonCommand = (process.env.PYTHON_CMD) ? process.env.PYTHON_CMD : 'python3'

// The default error response if something goes wrong
const defaultErrorResponse = { 'body': { 'error': 'An error occured while processing your request' }, 'status': 500 }


//
// Call a Python script
//
// Returns a promise!!! 'await' a JSON object
//
exports.run = function (script, arguments, image)
{
    return runScript(script, arguments, image)
}


//
// Handles the creation of the child process in which Python runs
//
function runPythonProcess(script, arguments, image)
{
    return new Promise((accept, reject) => {

        let imageSize = (image) ? image.size : 0

        // Create the process. Pass the script name and the number of bytes as command line arguments
        //
        const pythonProcess = spawn(pythonCommand, ['jsconnect.py', script, imageSize, JSON.stringify(arguments)])

        let result = ''
        let errResult = ''

        // Catch general errors
        //
        pythonProcess.on('error', (err) => {

            reject(err)
        })

        // Write the image data to the process's stdin buffer
        //
        if (pythonProcess.stdin)
        {
            if (image)
            {
                pythonProcess.stdin.write(image.data)

                pythonProcess.stdin.on('error', (err) => {

                    console.warn(`(${__filename}) ${err}`)
                })
            }
        }

        // Read response data
        //
        pythonProcess.stdout.on('data', (data) => {

            result += data
        })

        // Read error data
        //
        pythonProcess.stderr.on('data', (data) => {

            errResult += data
        })

        // The program is done. Return the results
        //
        pythonProcess.stdout.on('end', () => {

            if (errResult)
            {
                reject(errResult)
            }
            else
            {
                accept(result)
            }
        })
    })
}


//
// Calls the process creation function and parses its outputs
//
async function runScript(script, arguments, image)
{
    try
    {
        // Run Python code
        var output = await runPythonProcess(script, arguments, image)
    }
    catch (e)
    {
        return processReturnValue({ message: e, status: -1 })
    }

    try
    {
        // Parse output string as JSON
        var json = JSON.parse(output)
    }
    catch (e)
    {
        var json = { message: e.message, status: -2 }
    }

    // Reformat the JSON before returning it
    return processReturnValue(json)
}


//
// Processes the Python output into a format ready to be returned by the API,
// and logs any error messages.
//
// (Returns) A JSON object of the form:
//
//     { "body": <the response body>, "status": <the repsonse status code> }
//
function processReturnValue(val)
{
    if (typeof val.status === 'undefined' || val.status < 0)
    {
        if (val.message)
        {
            console.error(val.message)
        }

        return defaultErrorResponse
    }

    if (val.status === 0)
    {
        //
        // Exit Status 0: Success
        //

        if (!val.data)
        {
            console.error('"data" field missing from Python response')
            return defaultErrorResponse
        }

        return { 'body': val.data, 'status': 200 }
    }


    if (val.status === 1)
    {
        //
        // Exit Status 1: Unsupported or unknown file type
        //

        var statusCode = 444
    }
    else if (val.status === 2)
    {
        //
        // Exit Status 2: Supported image type not available...
        //

        var statusCode = 555
    }
    else if (val.status === 3)
    {
        //
        // Exit Status 3: Corrupted or unsafe image file
        //

        var statusCode = 445
    }
    else if (val.status === 4)
    {
        //
        // Exit Status 4: TorchServe failures
        //

        console.error(val.message)

        return defaultErrorResponse
    }
    else
    {
        //
        // Exit Status ?
        //

        console.error(`Unrecognized or invalid value for Python return status: ${val.status}`)
        return defaultErrorResponse
    }

    console.warn(val.message)
    return { 'body': { 'error': val.message }, 'status': statusCode }
}

