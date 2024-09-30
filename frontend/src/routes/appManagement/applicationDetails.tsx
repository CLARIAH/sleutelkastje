import axios from "axios";
import {
    useLoaderData,
} from "react-router-dom";
import {IApp} from "../root.tsx";
import {
    Box,
    Typography
} from "@mui/material";

interface IApplicationLoaderData {
    app: IApp,
}

export async function applicationLoader({params}: {params: any}) {

    const appName = (params as {appName: string}).appName;
    const detailsRequest = axios.get('/api/apps/' + appName + '/details')
    const detailsResult = await detailsRequest

    return {
        app: detailsResult.data.application,
    } as IApplicationLoaderData
}


export function ApplicationDetails() {
    const {app} = useLoaderData() as IApplicationLoaderData

    return <>
        <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>
            <Typography component="h2" variant="h2" sx={{mb: 2}}>
                {app.name}
            </Typography>
        </Box>
    </>
}
