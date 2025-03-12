import axios from "axios";
import { useEffect, useRef, useState } from "react";

function Corners({ imageSrc, imageFile, onSubmitCorners, mode }) {
    const canvasRef = useRef(null)
    const [image, setImage] = useState(null)
    const apiUrl = process.env.REACT_APP_API_URL;
    const [hasCorners, setHasCorners] = useState(false);
    const [imageRes, setImageRes] = useState({ x: 0, y: 0 })
    const isRotated = useRef(false);
    const originalCorners = useRef(null)

    const [corners, setCorners] = useState(null);

    const [draggingCorner, setDraggingCorner] = useState(null);
    const [scale, setScale] = useState({ x: 1, y: 1 });

    // Loading Icon
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        if (imageSrc) {
            console.log("Setting image source:", imageSrc);
            setImage(imageSrc);
        }

        // Find the button and trigger a click event
        setTimeout(() => {
            const submitButton = document.getElementById("sendData");
            if (submitButton) {
                submitButton.click();
            } else {
                console.warn("Submit Image button not found.");
            }
        }, 500); // Slight delay to ensure the button is available

    }, [imageSrc]);

    // useEffect(() => {
    //     if (imageFile) {
    //         console.log("Image file detected. Automatically extracting corners...");
    //         submitImage(); //   Automatically extract corners when the component loads
    //     }
    // }, [imageFile]);




    function getMousePosition(e) {
        let x, y;
        if (e.touches) {
            // Handling touch events
            const rect = canvasRef.current.getBoundingClientRect();
            const touch = e.touches[0] || e.changedTouches[0];
            x = (touch.clientX - rect.left) / scale.x;
            y = (touch.clientY - rect.top) / scale.y;
        } else {
            // Handling mouse events
            x = e.nativeEvent.offsetX / scale.x;
            y = e.nativeEvent.offsetY / scale.y;
        }
        return { x, y };
    }

    function handleMouseUp() {
        setDraggingCorner(null);
        drawToCanvas();  //   Ensure the color updates back to blue
    };

    function handleMouseMove(e) {
        if (draggingCorner !== null) {
            const { x, y } = getMousePosition(e);
            const newCorners = [...corners];
            newCorners[draggingCorner] = { x, y }
            setCorners(newCorners)
        }
    }

    function handleMouseDown(e) {
        const { x, y } = getMousePosition(e);
        const cornerIndex = corners.findIndex(
            // (corner) => Math.hypot(corner.x - x, corner.y - y) < 50
            (corner) => Math.hypot(corner.x - x, corner.y - y) < imageRes.x / 15  //   Larger touch area
        );
        if (cornerIndex !== -1) {
            setDraggingCorner(cornerIndex);
        }
    }

    //  Touch event handlers for mobile
    function handleTouchStart(e) {
        e.preventDefault();
        handleMouseDown(e);
    }

    function handleTouchMove(e) {
        e.preventDefault();
        // e.stopPropagation();
        handleMouseMove(e);
    }

    function handleTouchEnd(e) {
        e.preventDefault();
        handleMouseUp();
    }

    function drawQuad(context) {
        context.strokeStyle = "red";
        context.lineWidth = imageRes.x / 150;
        context.beginPath();
        context.moveTo(corners[0].x, corners[0].y);
        for (let i = 1; i < corners.length; i++) {
            context.lineTo(corners[i].x, corners[i].y);
        }
        context.closePath();
        context.stroke();

        context.fillStyle = "blue";
        corners.forEach((corner, index) => {
            context.beginPath();
            context.arc(corner.x, corner.y, imageRes.x / 25, 0, 2 * Math.PI)
            context.fillStyle = draggingCorner === index ? "green" : "blue";  //   Change to green while dragging
            context.fill();
        });
    };

    function scaleCanvas(imgWidth, imgHeight) {
        let maxWidth, maxHeight;
        let width = imgWidth;
        let height = imgHeight;

        if (width > height) {
            maxWidth = window.innerHeight * 0.80;
            maxHeight = window.innerWidth * 0.95;
        }
        else {
            maxWidth = window.innerWidth * 0.95;
            maxHeight = window.innerHeight * 0.80;
        }

        if (width > maxWidth) {
            const scaleFactor = maxWidth / width;
            width = maxWidth;
            height = height * scaleFactor
        }

        if (height > maxHeight) {
            const scaleFactor = maxHeight / height;
            height = maxHeight;
            width = width * scaleFactor
        }

        return { width, height };
    }

    function drawToCanvas() {
        const canvas = canvasRef.current
        const context = canvas.getContext("2d")

        if (image) {
            const img = new Image();
            img.src = image;
            img.onload = () => {
                setImageRes({ x: img.naturalWidth, y: img.naturalHeight })
                const { width, height } = scaleCanvas(img.naturalWidth, img.naturalHeight)

                if (width > height) {
                    isRotated.current = true;
                    setScale({ x: height / img.naturalHeight, y: width / img.naturalWidth })

                    canvas.width = img.naturalHeight;
                    canvas.height = img.naturalWidth;

                    canvas.style.width = `${height}px`
                    canvas.style.height = `${width}px`

                    context.clearRect(0, 0, canvas.width, canvas.height)
                    context.save();

                    context.translate(canvas.width, 0);
                    context.rotate(Math.PI / 2);


                    context.drawImage(img, 0, 0);

                    context.restore();

                    if (corners !== null)
                        drawQuad(context)
                }
                else {
                    setScale({ x: width / img.naturalWidth, y: height / img.naturalHeight })

                    canvas.width = img.naturalWidth;
                    canvas.height = img.naturalHeight;

                    canvas.style.width = `${width}px`
                    canvas.style.height = `${height}px`

                    context.clearRect(0, 0, canvas.width, canvas.height)
                    context.drawImage(img, 0, 0);
                    if (corners !== null)
                        drawQuad(context)
                }
            }
        } else {
            context.clearRect(0, 0, canvas.width, canvas.height);
        }
    }

    async function submitImage() {
        if (!imageFile) {
            console.error("No image file provided!");
            return;
        }

        const formData = new FormData();
        formData.append("image", imageFile);

        try {
            const response = await axios.post(apiUrl.concat("/corners"), formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            console.log("These are the corner values provided by preprocessing:");
            console.log(response.data.corner_points);

            let processedCorners = response.data.corner_points;

            if (isRotated.current) {
                originalCorners.current = processedCorners;
                processedCorners = [
                    { x: imageRes.y - processedCorners[0].y, y: processedCorners[0].x },
                    { x: imageRes.y - processedCorners[1].y, y: processedCorners[1].x },
                    { x: imageRes.y - processedCorners[2].y, y: processedCorners[2].x },
                    { x: imageRes.y - processedCorners[3].y, y: processedCorners[3].x }
                ];
            }

            setCorners(processedCorners);
            setHasCorners(true);

            // //   Ensure `drawToCanvas()` runs AFTER `setCorners` updates
            // setTimeout(() => {
            //     requestAnimationFrame(drawToCanvas);
            // }, 0);

        } catch (error) {
            console.error("Could not extract corners!", error);

            // Default corners if extraction fails
            setCorners([
                { x: 500, y: 500 },
                { x: 1000, y: 500 },
                { x: 1000, y: 1000 },
                { x: 500, y: 1000 }
            ]);
            setCorners(null)
            setHasCorners(true);
        }
    }

    async function submitCorners() {
        if (!corners || !imageFile) return;

        const formData = new FormData();
        formData.append('image', imageFile);

        if (isRotated.current) {
            console.log("These are the corner values BEFORE an inverse rotation is applied:");
            console.log(corners);

            formData.append("corners", JSON.stringify([
                { x: corners[0].y, y: imageRes.y - corners[0].x },
                { x: corners[1].y, y: imageRes.y - corners[1].x },
                { x: corners[2].y, y: imageRes.y - corners[2].x },
                { x: corners[3].y, y: imageRes.y - corners[3].x }
            ]));
        } else {
            formData.append("corners", JSON.stringify(corners));
        }

        setLoading(true);
        setProgress(0); // Start from 0%

        console.log("These are the corner values that will be submitted to the backend:");
        console.log(JSON.parse(formData.get("corners")));

        try {
            // const response = await axios.post(apiUrl.concat('/bce'), formData);

            const response = await axios.post(apiUrl.concat(`/${mode}`), formData, {
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    setProgress(percentCompleted);
                }
            });

            console.log("Here is the rider data:");
            console.log(response.data);

            //   Send API response back to getphotoBCE.js
            if (onSubmitCorners) {
                onSubmitCorners(response.data);
            }
        } catch (error) {
            console.error("Error submitting corners to BCE:", error);
        } finally {
            setHasCorners(false);
            setLoading(false);
        }
    }



    useEffect(() => {
        drawToCanvas();
        window.addEventListener("resize", drawToCanvas);
        return () => window.removeEventListener("resize", drawToCanvas);
    }, [draggingCorner, image, corners])



    return (
        <>
            {/* Loading Overlay */}
            {loading && (
                <div className="loading-overlay">
                    <div className="spinner"></div>
                    <p className="loading-text">Loading... {progress}%</p>
                </div>
            )}

            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossOrigin="anonymous"></link>
            <div className="container">
                {/* <br /><br /> */}

                {hasCorners ? (
                    <div className="row">
                        <h2 style={{textAlign: "center"}}>Adjust Corners If Needed</h2>
                    </div>
                ) : (
                    <div className="row">
                        <h1>Extracting Corners...</h1>
                    </div>
                )}
                <div className="row">
                    <div className="col">
                        <canvas
                            // className="mt-5"
                            onMouseDown={handleMouseDown}
                            onMouseMove={handleMouseMove}
                            onMouseUp={handleMouseUp}
                            onTouchStart={handleTouchStart}  //   Added touch support
                            onTouchMove={handleTouchMove}
                            onTouchEnd={handleTouchEnd}
                            ref={canvasRef}
                            style={{
                                borderRadius: "10px",
                                boxShadow: "0px 4px 8px rgba(0,0,0,0.2)",
                            }}
                        // style={{ cursor: "crosshair", maxWidth: "100%" }}
                        // style={{
                        //     cursor: "crosshair",
                        //     width: "95vw", // 🔹 Ensure it fits well within the screen width
                        //     height: "auto",
                        //     maxWidth: "100%",
                        //     maxHeight: "90vh",
                        //     touchAction: "none",  // 🔹 Prevents page scrolling while dragging
                        //     border: "2px solid black",  // 🔹 Keeps it visible
                        // }}
                        />
                    </div>
                </div>

                <div className="row">
                    {(imageFile !== null && hasCorners) && (
                        <div className="button-container">
                            <button className="corner-button" id="sendData" onClick={submitCorners}>
                                Continue
                            </button>
                        </div>
                    )}
                    {(imageFile !== null && !hasCorners) && <button className="btn btn-primary" id="sendData" onClick={submitImage} style={{ display: "none" }}>Submit Image and Extract Corners</button>}

                </div>

            </div>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossOrigin="anonymous"></script>
        </>
    )
}

export default Corners