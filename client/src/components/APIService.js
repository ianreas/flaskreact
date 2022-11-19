export default class APIService {

    static async PickTicker(ticker) {
        return await fetch('/acceptStockTicker', {
            'method' : 'POST', 
            headers: {
                'Content-Type' : 'application/json'
            }, 
            body: JSON.stringify(ticker)
        })
        .then(response => response.json()
        )
        .catch(error => console.log(error + " AAAA fuck me"))
    }
}