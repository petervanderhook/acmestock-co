import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://stinky.westus3.cloudapp.azure.com:8100/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div class='latest-stats-div'>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<td><h5>Average Shares Available per Company Stock:</h5></td>
                            <td>{stats['average_shares_available_per_stock']}</td>
                        </tr>
                        <tr>
							<td><h5>Average price per all available shares:</h5></td> 
                            <td>{stats['average_stock_price']}</td>
						</tr>
                        <tr>
							<td><h5>Total number of Sell Orders Listed:</h5></td> 
                            <td>{stats['num_sell_orders_listed']}</td>
						</tr>
                        <tr>
							<td><h5>Total number of Stocks Listed:</h5></td> 
                            <td>{stats['num_stocks_listed']}</td>
						</tr>
                        <tr>
							<td><h5>Total number of Shares Available:</h5></td> 
                            <td>{stats['total_shares_available']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>
            </div>
        )
    }
}
