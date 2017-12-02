const express   = require('express')
, app           = express()
, bodyParser    = require('body-parser')
, cors          = require('cors')
, config        = require('./config/config.json')
, Session       = require('./modules/session')
, Coins       = require('./modules/coins')

// base server setup
const port = process.env.PORT || config.server.port
const baseRoute = `/api/${config.server.version}`

// setup the middlewares
app.disable('x-powered-by')
app.use(bodyParser.urlencoded({ extended: true }))
app.use(bodyParser.json())
app.use(cors({
  methods: ['GET', 'PUT', 'POST'],
}))

// router handlers, uses Session middleware
app.use(`${baseRoute}/coins`, Session, Coins)

// catchall
app.use('*', function(req, res) {
  res.status(404).send('Nothing here! Donate me some ETH: 0x2eeD2C4Cb8243ecE8866b8f1A87f469e1cfc638F')
})

// =============================================================================
// START THE SERVER
// =============================================================================
app.listen(port)
console.log(`Server Started\nhttp://localhost:${port}`)
