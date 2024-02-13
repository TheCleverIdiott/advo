import { RouteObject } from "react-router-dom";
import Authentication from "../pages/Authentication";
import IndividualSearchPage from "../pages/IndividualSearchPage/IndividualSearchPage";
import Main from "../pages/Main";
import Search from "../pages/Search/Search";
import User from "../pages/User/User";
import JudgementSearch from "../pages/judgmentSearch/judgmentSearch";

const routes : RouteObject[] = [
    {
        path: "/user",
        element : <User />
    },
    // {
    //     path: "/",
    //     element : <Authentication />
    // },
    {
        path: "/search",
        element : <Search />
    },
    {
        path : "/authentication",
        element: <Authentication />
    },
    {
        path : "/",
        element: <Authentication />
    }
    ,
    {
        path : "/document/:documentID",
        element: <IndividualSearchPage />
    },
    {
        path: "/judgementsearch",
        element: <JudgementSearch/>
    }


]

export default routes