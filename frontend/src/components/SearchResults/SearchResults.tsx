import React from 'react'
import ResultCard from '../ResultCard/ResultCard';
import styles from "./SearchResults.module.scss";

const SearchResults = ( datas : any) => {

  console.log("search result data" , datas);

  if(datas.length === 0) return <div>no results</div>
  

  return (
    <div >
        
        <div className={styles.results}>
          data
           {/* {datas?.map(() => {

           })} */}
        </div>
    </div>
  )
}

export default SearchResults