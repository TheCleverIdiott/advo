const auth = (req, res, next) => {
    if (req.session.isLoggedIn === true) {
        req.User = req.session.User
        next()

    }else {
        console.log("not logged");
        res.redirect('/login')
    }
 
}

module.exports = auth