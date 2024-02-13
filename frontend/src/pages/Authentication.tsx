import React from 'react'
import Login from '../components/Authentication/Login'
import Register from '../components/Register/Register'

const Authentication = () => {
  const [showState, setShowState] = React.useState("Register")
  return (
    <div style={{
      display :"flex",
      justifyContent:"center",
      alignItems: "center",
      boxSizing :"border-box",
      padding: "0 4rem"
    }}>

      {
        showState === "Register" ? 
        (<Register state = {setShowState} />):
        (
          <Login state = {setShowState}  />
        )
      }
        {/* <Login /> */}
         

        <img style={{
          height:"700px"
        }} src = {process.env.PUBLIC_URL + '/images/court.jpg'} alt='no image' />
    </div>
  )
}

export default Authentication