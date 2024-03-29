import React, { useEffect, useState } from 'react'
import '../App.css';

export default function EndpointAudit(props) {
    const [isLoaded, setIsLoaded] = useState(false);
    const [log, setLog] = useState(null);
    const [error, setError] = useState(null)
	const rand_val = Math.floor(Math.random() * 100); // Get a random event from the event store
    const [index, setIndex] = useState(null);
    const getAudit = () => {
        fetch(`http://stinky.westus3.cloudapp.azure.com:80/audit/${props.endpoint}?index=${rand_val}`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Audit Results for " + props.endpoint)
                setLog(result);
                setIndex(rand_val);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
	useEffect(() => {
		const interval = setInterval(() => getAudit(), 4000); // Update every 4 seconds
		return() => clearInterval(interval);
    }, [getAudit]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        let a = JSON.stringify(log)
        if (props.endpoint === 'get_stock_quantity') {
            return (
                <div class='div-quantity'>
                    <h3>{props.endpoint}-{index}</h3>
                    {a}
                </div>
            )
        } 
        return (
            <div class='div-price'>
                <h3>{props.endpoint}-{index}</h3>
                {a}
            </div>
        )
    }
}
