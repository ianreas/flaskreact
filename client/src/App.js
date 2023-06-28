import React from 'react'
import Navbar from './components/Navbar'
import './styles/globals.css'
import { Route, Switch } from 'react-router-dom'
import Home from './pages/Home'
import About from './pages/About'
import Contact from './pages/Contact'
import Spy from './pages/Spy'
import NewSpy from './pages/NewSpy'



export default function App() {
  /*
  //this shit will receive data from flask so it can be displayed on react
  useEffect(() => {
    fetch(`/acceptStockTicker?ticker=${ticker}`).then(
      res => res.json()
    ).then(
      data => {
        setData(data)
        console.log(data.data)
      }
    )
  }, []) 
  */
  


  /*
  var responseClone; // 1
fetch('/acceptStockTicker')
.then((res) => {res.json() 
    responseClone = response.clone(); // 2
    return response.json();}
)
.then(function (data) {
    // Do something with data
}, function (rejectionReason) { // 3
    console.log('Error parsing JSON from response:', rejectionReason, responseClone); // 4
    responseClone.text() // 5
    .then(function (bodyText) {
        console.log('Received the following instead of valid JSON:', bodyText); // 6
    });
});



onSubmit={async () => {
                const response = await fetch("/acceptStockTicker", {
                    method: 'POST', 
                    headers: {
                        "Content-Type": 'application/json'
                    },
                    body: JSON.stringify({ticker})
                })
                if (response.ok) {
                    console.log("response worked " + response)
                    setTicker("")
                } else {
                  console.log('fuck u')
                }
            }}

*/

  //const pickedTicker = (ticker) => {
    //setTicker(ticker)
  //}

  

  return (
    <div>
      <Navbar />
      <div className='container'>
        <Switch>
          <Route path='/' ><Home /></Route>
          <Route path='/contact'><Contact /></Route>
          <Route path='/about'><About /></Route>
          <Route path='/Spy'> <Spy/></Route>
          <Route path='/NewSpy'><NewSpy /></Route>
        </Switch>
      </div>
    </div>
  )
}
