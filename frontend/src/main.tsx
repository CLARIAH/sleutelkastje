import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import {createBrowserRouter, RouterProvider} from "react-router-dom";
import ErrorPage from "./components/ErrorPage.tsx";
import {Root, loader as rootLoader} from "./routes/root.tsx";
import {Index} from "./routes";
import axios from "axios";
import Login from "./routes/authentication/login.tsx";
import {CompleteProfile, completeProfileLoader} from "./routes/authentication/completeProfile.tsx";
import {ApplicationDetails, applicationLoader} from "./routes/appManagement/applicationDetails.tsx";
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import '@fontsource/victor-mono/100.css';
import {ApplicationInvitations, invitationsLoader} from "./routes/appManagement/applicationInvitations.tsx";
import {ApplicationItems, itemsLoader} from "./routes/appManagement/applicationItems.tsx";
import {Invitation, invitationLoader} from "./routes/invitation.tsx";
import {ApiKeys, apiKeysLoader} from "./routes/user/apiKeys.tsx";
import {getBackendBase} from "./config.ts";
import {Profile} from "./routes/user/profile.tsx";


axios.defaults.baseURL = getBackendBase()
axios.defaults.withCredentials = true

const router = createBrowserRouter([
    {
        path: "/login",
        element: <Login />
    },
    {
        path: "/complete-profile",
        element: <CompleteProfile />,
        loader: completeProfileLoader
    },
    {
        path: '/invitations/:invitationCode',
        element: <Invitation />,
        loader: invitationLoader,
        errorElement: <ErrorPage />,
    },
    {
        path: "/",
        element: <Root />,
        loader: rootLoader,
        errorElement: <ErrorPage />,
        children: [
            {
                index: true,
                element: <Index />
            },
            {
                path: '/apps/:appName',
                element: <ApplicationDetails />,
                loader: applicationLoader,
            },
            {
                path: '/apps/:appName/invitations',
                element: <ApplicationInvitations />,
                loader: invitationsLoader,
            },
            {
                path: '/apps/:appName/items',
                element: <ApplicationItems />,
                loader: itemsLoader,
            },
            {
                path: "/keys",
                element: <ApiKeys />,
                loader: apiKeysLoader,
            },
            {
                path: "/profile",
                element: <Profile />,
            }
        ]
    }
])

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <RouterProvider router={router} />
    </StrictMode>,
)
