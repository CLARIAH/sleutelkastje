import axios from "axios";
import {
    useLoaderData,
} from "react-router-dom";
import {IApp} from "../root.tsx";
import {
    Box,
    Typography
} from "@mui/material";
import {ItemsTable} from "../../components/ItemsTable.tsx";


export interface IItem {
    id: number
    name: string
}

interface IItemsLoaderData {
    app: IApp
    items: IItem[]
}

export async function itemsLoader({params}: {params: any}) {

    const appName = (params as {appName: string}).appName;

    const detailsRequest = axios.get('/api/apps/' + appName + '/details')
    const itemsRequest = axios.get('/api/apps/' + appName + '/items')

    const detailsResult = await detailsRequest
    const itemsResult = await itemsRequest

    return {
        app: detailsResult.data.application,
        items: itemsResult.data.items
    } as IItemsLoaderData
}


export function ApplicationItems() {
    const {app, items} = useLoaderData() as IItemsLoaderData

    return <>
        <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>
            <Typography component="h2" variant="h2" sx={{mb: 2}}>
                {app.name}
            </Typography>
            <ItemsTable app={app} items={items} />
        </Box>
    </>
}
