import {FullpageFormContainer} from "../components/FullpageFormContainer.tsx";
import {Button, Stack, Typography} from "@mui/material";
import axios from "axios";
import {useLoaderData, useNavigate} from "react-router-dom";

interface IInvitationDetails {
    appName: string
    appId: string
    role: string
    code: string
}

interface IInvitationLoaderData {
    invitation: IInvitationDetails
}

enum InvitationAction {
    accept = 'accept',
    reject = 'reject'
}

export async function invitationLoader({params}: {params: any}) {
    const invitationCode = (params as {invitationCode: string}).invitationCode
    const response = await axios.get('/api/apps/invitations/' + invitationCode)

    return {
        invitation: response.data
    } as IInvitationLoaderData
}

export function Invitation() {

    const {invitation} = useLoaderData() as IInvitationLoaderData
    const navigate  = useNavigate()

    function submitRequest(action: InvitationAction) {
        axios.post('/api/apps/invitations/' + invitation.code, {
            action: action
        }).then(response => {
            console.log(response)
            navigate('/apps/' + invitation.appId)
        })
    }

    return <FullpageFormContainer>
        <Typography
            component="h1"
            variant="h4"
            sx={{ width: '100%', fontSize: 'clamp(2rem, 10vw, 2.15rem)' }}
        >
            Accept Invitation
        </Typography>
        <Typography
            component="h2"
            variant="h6"
            >
            You are invited to join application {invitation.appName}.
        </Typography>
        <Typography>Your role will be <strong>{invitation.role}</strong></Typography>
        <Stack sx={{mt: 4}} direction="row" spacing={2}>
            <Button
                fullWidth
                variant="outlined"
                color={'error'}
                onClick={() => submitRequest(InvitationAction.reject)}
            >
                Decline
            </Button>
            <Button
                fullWidth
                sx={{mt: 4}}
                variant="contained"
                onClick={() => submitRequest(InvitationAction.accept)}
            >
                Accept
            </Button>
        </Stack>
    </FullpageFormContainer>
}
