const express = require('express');
const upload = require('../multer/index')
const route = new express.Router()
const path = require('path');


const {postLogin} = require('../controllers/auth.controller')
const {postRegister} = require('../controllers/auth.controller')
const {getDocument} = require('../controllers/auth.controller')

const auth = require('../middleware/auth');
const User = require('../models/user.model');



route.post('/register', postRegister)
route.post('/login', postLogin)
route.get('/fetch/:id', getDocument)


route.post('/delete', (req, res) => {
    User.deleteMany({})
    .then((user) => {
        if(!user) {
            return res.status(404).send('error')
        }
        res.status(200).send('deleted')
    })
})
route.get('/fetch', (req, res) => {
    User.find({})
    .then((user) => {
        if(!user) {
            return res.status(404).send('error')
        }
        res.status(200).send(user)
    })
})

module.exports = route