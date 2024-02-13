import { useMutation, useQuery } from "@tanstack/react-query";
import { AxiosResponse } from "axios";
import { useState } from "react";
import { useNavigate } from "react-router";
import api, { authHeader } from "./index";

// export const FetchSearchQuery = () => {
//   return useMutation((tags: string[]) => {
//     return api.post("/search", tags);
//   });
// };

export function useLoginQuery() {
  const navigate = useNavigate();
  return useMutation((data: any) => api.post("/login", data), {
    onSuccess: (res: AxiosResponse) => {
      console.log(res);

      localStorage.setItem("LicenseKey", res.data?.licenseID);
      navigate("/user");
      // setShow("setup");
    },
  });
}

export function useRegisterUser() {
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const {
    isLoading,
    isSuccess,
    isError,
    mutate: handleRegister,
  } = useMutation((registerData: any) => api.post("/register", registerData), {
    onSuccess: (res) => {
      localStorage.setItem("LicenseKey", res.data?.licenseID);
      navigate("/user");
    },
    onError: (err: any) => {
      setError(err.response.data.message);
    },
  });
  return { isLoading, isSuccess, isError, error, handleRegister };
}
