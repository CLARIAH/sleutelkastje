import {IApp, IUserData} from "../root.tsx";
import axios from "axios";
import {useLoaderData} from "react-router-dom";
import {InvitationsTable} from "../../components/InvitationsTable.tsx";
import {Box, Typography} from "@mui/material";
import {IItem} from "./applicationItems.tsx";

export interface IInvitation {
    id: number,
    user: IUserData|null
    role: string
}

interface IInvitationsLoaderData {
    app: IApp
    invitations: IInvitation[]
    items: IItem[]
}

export async function invitationsLoader({params}: {params: any}) {

    const appName = (params as {appName: string}).appName;

    const detailsRequest = axios.get('/api/apps/' + appName + '/details')
    const invitationsRequest = axios.get('/api/apps/' + appName + '/invitations')
    const itemsRequest = axios.get('/api/apps/' + appName + '/items')

    const detailsResult = await detailsRequest
    const invitationsResult = await invitationsRequest
    const itemsResult = await itemsRequest

    return {
        app: detailsResult.data.application,
        invitations: invitationsResult.data.invites,
        items: itemsResult.data.items,
    } as IInvitationsLoaderData
}

export function ApplicationInvitations() {
    const {app, invitations, items} = useLoaderData() as IInvitationsLoaderData

    return <>
        <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>
            <Typography component="h2" variant="h2" sx={{mb: 2}}>
                Invitations for {app.name}
            </Typography>
            <InvitationsTable app={app} invitations={invitations} items={items} />
        </Box>
    </>
}
