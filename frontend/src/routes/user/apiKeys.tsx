import {Box, Typography} from "@mui/material";
import axios from "axios";
import {useLoaderData, useOutletContext} from "react-router-dom";
import {ApiKeysTable} from "../../components/ApiKeysTable.tsx";
import {IApp} from "../root.tsx";


export interface IApiKey {
    name: string
}

interface IApiKeysLoaderResult {
    keys: IApiKey[]
}

export async function apiKeysLoader() {
    const response = await axios.get("/api/keys")

    return {keys: response.data.keys} as IApiKeysLoaderResult
}

export function ApiKeys() {

    const {keys} = useLoaderData() as IApiKeysLoaderResult
    const {apps} = useOutletContext() as {apps: IApp[]}

    return <>
        <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>
            <Typography component="h2" variant="h2" sx={{mb: 2}}>
                Manage API keys
            </Typography>
            <ApiKeysTable keys={keys} apps={apps} />
        </Box>
    </>
}
