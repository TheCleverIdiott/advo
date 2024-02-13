import { useMutation, useQuery } from "@tanstack/react-query";
import api, { authHeader , apiML } from "./index";

export const FetchSearchQuery = () => {
  return useMutation((documentID: string) => {
    const data = {
      id : documentID,
      spell : "false"
    }
    return apiML.post("/update",data );
  });
};

export const FetchMySubmission = () => {
  return useMutation((licenseID: string) => {
    const data = {
      licenseID : licenseID,
      
    }
    return apiML.post("/alldocuments",data );
  });
};

// export const FetchMySubmission = (licenseID: string | null) => {
//   const {isLoading , isError , data : datas} = useQuery([`fetchSubmission ${licenseID}`],async() => {
//     const res: any = await api.get(`/fetch/${licenseID}`);
      
      
//       return res;
//   } )

//   return datas
// }

