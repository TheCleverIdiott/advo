const multer = require('multer');
const path = require('path');

let storage = multer.diskStorage({
    destination: function (req, file, cb) {
  
        cb(null, "uploads")
    },
    filename: function (req, file, cb) {
        cb(null, file.fieldname + '-' + Date.now())
    }
  })
       

let upload = multer({ 
    storage: storage,
    fileFilter: function (req, file, cb){
    
        // Set the filetypes, it is optional
        var filetypes = /jpeg|jpg|png|pdf/;
        var mimetype = filetypes.test(file.mimetype);
  
        var extname = filetypes.test(path.extname(
                    file.originalname).toLowerCase());
        
        if (mimetype && extname) {
            return cb(null, true);
        }
      
        cb("Error: File upload only supports the "
                + "following filetypes - " + filetypes);
      } 

})

module.exports = upload
