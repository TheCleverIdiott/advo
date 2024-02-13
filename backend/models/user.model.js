const mongoose = require('mongoose')

const userSchema = new mongoose.Schema({
    licenseID: {
        type: String,
        required: true,
        unique: true
    },
    name: {
        type: String,
        required: true
    },
    mobile: {
        type: String,
        required: true,
        unique: true
    },
    password: {
        type: String,
        required: true
    },
    designation: {
        type: String,
        required: true
    },
    file: {
        data: Buffer,
        contentType: String
    },
    verified: {
        type: Boolean,
        default: false
    }
    

})

const User = mongoose.model('User', userSchema)

module.exports = User