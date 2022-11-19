import React, {useState, useEffect} from 'react'
import Form from './components/Form'



function App() {
  const [ticker, setTicker] = useState("")
  const [data, setData] = useState([{}])

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

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!ticker) return

    async function fetchData() { const response = await fetch(`/acceptStockTicker?ticker=${ticker}`)
    const data = await response.json()
    setData(data)
  }
  fetchData()
 } 


  return (
    <div>
      <div>
            <form onSubmit={handleSubmit}>
            <label htmlFor="title" className="form-label">Ticker</label>
            <input 
            type="text"
            className="form-control" 
            placeholder ="Enter stock ticker"
            value={ticker}
            onChange={(e)=>setTicker(e.target.value)}
            required
            />
            <input type='submit' value='Submit'/>
            </form>

        </div>

    <div dangerouslySetInnerHTML={{__html: data.data}}>
      
    </div>
    </div>
  )
}

export default App