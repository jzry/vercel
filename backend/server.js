const app = require('./index')

const port = process.env.PORT
const protocol = process.env.PROTOCOL


if (protocol.toLowerCase() === 'https')
{
    const https = require('https')
    const fs = require('fs')

    const config = {
        key: fs.readFileSync(process.env.KEY_FILE),
        cert: fs.readFileSync(process.env.CERT_FILE),
    }

    // Create the https server with the certificate and key
    const server = https.createServer(config, app)

    server.listen(port, () => {
        let timestamp = new Date()
        console.log(`${timestamp}\t| Server listening on port ${port}`)
    })
    .on('error', (err) => {
        let timestamp = new Date()
        console.log(`${timestamp}\t| Server failed to start (port ${port})`)
        console.error(err)
    })

    const express = require('express')

    let http = express()

    // Redirect http to https
    http.get('*', (req, res) => {
        res.redirect(301, 'https://' + req.headers.host + req.url)
    })

    // Listen on port 80
    http.listen(80)
}
else
{
    // 8080 is the port we are using in the meantime, but may be changed later (probably)
    app.listen(port, () => {
        let timestamp = new Date()
        console.log(`${timestamp}\t| Server listening on port ${port}`)
    })
    .on('error', (err) => {
        let timestamp = new Date()
        console.log(`${timestamp}\t| Server failed to start (port ${port})`)
        console.error(err)
    })
}

