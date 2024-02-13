
const express = require('express');

const route = new express.Router()

const {postDoc} = require('../controllers/docs.controller')
const {getDoc} = require('../controllers/docs.controller')
const {getDocs} = require('../controllers/docs.controller')
const {deleteDoc} = require('../controllers/docs.controller')
const {updateDoc} = require('../controllers/docs.controller')

const auth = require('../middleware/auth');

route.post('/post', postDoc)
route.get('/get/:id', getDoc)
route.get('/get', getDocs)
route.delete('/delete/:id', deleteDoc)
route.patch('/update/:id', updateDoc)



module.exports = route
