import { useMutation, useQuery } from "@tanstack/react-query";
import api, { authHeader , apiML } from "./index";

export const FetchSearchQuery = () => {
  return useMutation((tags: string[]) => {

    const data = {
      search_key : tags
    }

    return apiML.post("/search", data);
  });
};

export const FetchSearchQuery2 = () => {
  return useMutation((value: string) => {

    const data = {
      search_key : value
    }

    return apiML.post("/search", data);
  });
};


export const AutomaticQuery = () => {
  return useMutation((tags: string[]) => {

    const data = {
      search_key : tags
    }

    return apiML.post("/search", data);
  });
};

export const SearchIndividualQuery = (documentID : string) => {
    const {data , isLoading , isError} = useQuery([`/fetch/${documentID}`]   , async () => {
      const res: any = await api.get(`/fetch/${documentID}`);
      console.log(res);
      
      return res;
    },)
}

export const AutoCompleteQuery = () => {
  const {data : datas , isLoading , isError} = useQuery([`autocomplete`]   , async () => {
    const res: any = await apiML.get(`/autocomplete?limit=1000&sort=True`);
    
    
    return res;
  },)

  console.log(datas);
  

  const newArray = datas?.data?.keywords.map((data: string , index: number) => {
    return {
      label: data,
      value : data
    }
  })

  return newArray
}
