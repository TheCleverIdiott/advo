import { AxiosError } from "axios";
import { IconContext } from "react-icons";
import { MutationCache , QueryClient ,QueryClientProvider} from "@tanstack/react-query";
import { message } from "antd";
import "./App.css"

// import { MutationCache, QueryClient } from "react-query";
// import { QueryClientProvider } from "react-query/types/react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import routes from "./utils/routes";

const router = createBrowserRouter(routes);




export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
  // queryCache: new QueryCache({
  //   onError: (err: any, query: Query) => {
  //     console.log(err.response?.data?.message);
  //     if (!["auth/setup-workspace"]) message.error(query);
  //   },
  // }),
  mutationCache: new MutationCache({
    onError: (err) => {
      const error = err as AxiosError;
      const routeList = [
        "/auth/login",
      ];
      if (error.message?.toLowerCase() !== "jwt expired") {
        if (error?.config?.url && !routeList.includes(error?.config?.url)) {
          // message.error(error.message?.replace("Error:", "").toSentenceCase());
        }
      }
    },
  }),
});

function AppRoutes() {
  return(
    <QueryClientProvider client={queryClient}>
      <IconContext.Provider value={{style : {verticalAlign: "middle"}}} >
        <RouterProvider router={router} />

      
      </IconContext.Provider>
    </QueryClientProvider>
  )
}

export default AppRoutes