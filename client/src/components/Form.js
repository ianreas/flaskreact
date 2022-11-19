import React, {useState} from 'react'
import APIService from './APIService'

const Form = (props) => {
    const [ticker, setTicker] = useState("")

   

    return (
        <div>
            <form onSubmit={async () => {
                const response = await fetch("/acceptStockTicker", {
                    method: 'POST', 
                    headers: {
                        "Content-Type": 'application/json'
                    },
                    body: JSON.stringify({ticker})
                })
                if (response.ok) {
                    console.log("response worked")
                    setTicker("")
                }
            }}>
            <label htmlFor="title" className="form-label">Ticker</label>
            <input 
            type="text"
            className="form-control" 
            placeholder ="Enter stock ticker"
            value={ticker}
            onChange={(e)=>setTicker(e.target.value)}
            required
            />
            </form>
        </div>
    )
}

export default Form

 /*const pickTicker = () => {
        APIService.PickTicker({ticker})
        .then((response) => {props.pickedTicker(response) 
        console.log(response)})
        .catch(error => console.log('error', error))

        
    }

    const handleSubmit=(event)=>{
        event.preventDefault()
        pickTicker()
        console.log(ticker)
        setTicker("")
        
    }
    */