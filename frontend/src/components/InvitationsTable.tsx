import {
    Autocomplete,
    Box,
    Button,
    Dialog, DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    FormControl,
    IconButton,
    Input,
    InputAdornment,
    InputLabel,
    Paper,
    Step,
    StepLabel,
    Stepper,
    TextField,
    Typography
} from "@mui/material";
import {DataGrid, GridColDef, GridRowSelectionModel, GridToolbarContainer} from '@mui/x-data-grid';
import {FormEvent, useState} from "react";
import axios from "axios";
import {useRevalidator} from "react-router-dom";
import DeleteIcon from '@mui/icons-material/Delete';
import SendIcon from '@mui/icons-material/Send';
import {ContentCopyRounded} from "@mui/icons-material";
import {IApp} from "../routes/root.tsx";
import {IInvitation} from "../routes/appManagement/applicationInvitations.tsx";
import {NoResultsOverlay} from "./NoResultsOverlay.tsx";
import {NoRowsOverlay} from "./NoRowsOverlay.tsx";
import {IItem} from "../routes/appManagement/applicationItems.tsx";

const columns: GridColDef[] = [
    {field: 'id', headerName: 'ID', width: 70},
    {field: 'role', headerName: 'Role', width: 100},
    {
        field: 'status',
        headerName: 'Status',
        width: 100,
        valueGetter: (_value, row) => row.user == null ? `Pending` : `Accepted`,
    },
    {
        field: 'user',
        headerName: 'User',
        width: 300,
        valueGetter: (_value, row) => row.user != null ? row.user.nickname : ``,
    }
]

export function InvitationsTable({app, invitations, items}: {app: IApp, invitations: IInvitation[], items: IItem[]}) {

    const [showModal, setShowModal] = useState(false)
    const [inviteCode, setInviteCode] = useState<string | null>('')
    const [role, setRole] = useState('')
    const [activeTab, setActiveTab] = useState(0)
    const revalidator = useRevalidator()
    const [selectedItems, setSelectedItems] = useState<IItem[]>([])

    const [rowSelection, setRowSelection] = useState<GridRowSelectionModel>([])

    function handleCloseModal() {
        setShowModal(false)
        setActiveTab(0)
        setRole('')
    }

    function createInvitation(e: FormEvent) {
        e.preventDefault()

        let itemRoles: Record<string, string> = {}

        selectedItems.forEach((item) => {
            // @ts-ignore
            itemRoles[item.name] = e.target[item.name + '-role'].value
        })

        console.log("Item Roles", itemRoles)

        axios.post('/api/apps/' + app.mnemonic + '/invitations', {
            role: role,
            itemRoles: itemRoles,
        }).then(response => {
            console.log(response)
            setInviteCode(response.data.inviteId)
            setActiveTab(1)
            revalidator.revalidate()
        })
    }

    function deleteInvitations() {
        axios.post('/api/apps/' + app.mnemonic + '/invitations/bulk-delete', {
            data: {
                ids: rowSelection,
            }
        }).then((_response) => {
            revalidator.revalidate()
        })
    }

    function InvitationsToolbar() {
        return (
            <GridToolbarContainer>
                <Button onClick={() => setShowModal(true)} endIcon={<SendIcon />} >Create invitation</Button>
                <Box sx={{flexGrow: 1}} />
                <Button onClick={deleteInvitations} color={'error'} startIcon={<DeleteIcon />} disabled={rowSelection.length == 0} >Delete</Button>
            </GridToolbarContainer>
        )
    }

    function renderModalContent() {
        switch (activeTab) {
            case 0:
                return <Box component={"form"} onSubmit={createInvitation}>
                    <DialogContent>
                        <DialogContentText>
                            Create an invitation
                        </DialogContentText>
                        <Box sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            width: '100%',
                            gap: 2
                        }}>
                            <TextField required name={"invitationRole"} id={"invitationRole"} value={role} onChange={e => setRole(e.target.value)} label={"Role"} variant={"standard"} />
                            <Autocomplete
                                multiple
                                options={items}
                                getOptionLabel={(option) => option.name}
                                renderInput={(params) => (
                                    <TextField {...params} label={'Items'} variant={'standard'} />
                                )}
                                value={selectedItems}
                                onChange={(_e, newValue) => {setSelectedItems(newValue)}}
                                />
                            {selectedItems.map((item) => (
                                <TextField
                                    key={item.name}
                                    id={item.name + '-role'}
                                    name={item.name + '-role'}
                                    label={"Role for " + item.name}
                                    variant={'standard'}
                                    required />
                            ))}
                        </Box>
                    </DialogContent>
                    <DialogActions>
                        <Button type={'submit'}>Create</Button>
                    </DialogActions>
                </Box>
            case 1:
                const inviteUrl = window.location.origin + '/invitations/' + inviteCode
                return <>
                    <DialogContent>
                        <DialogContentText sx={{mb: 2}}>
                            Invitation created
                        </DialogContentText>
                        <DialogContentText sx={{mb: 2}}>
                            Send the following link to the user you wish to invite.
                        </DialogContentText>
                        <FormControl fullWidth sx={{m: 1}}>
                            <InputLabel htmlFor="invite-code">Link</InputLabel>
                            <Input
                                id={'invite-code'}
                                type={'text'}
                                value={inviteUrl}
                                disabled
                                endAdornment={
                                    <InputAdornment position={'end'}>
                                        <IconButton onClick={() => {navigator.clipboard.writeText(inviteUrl)}} aria-label={"Copy to clipboard"}>
                                            <ContentCopyRounded />
                                        </IconButton>
                                    </InputAdornment>
                                }
                            />
                        </FormControl>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleCloseModal}>Close</Button>
                    </DialogActions>
                </>
        }
    }

    return <>
        <Typography sx={{mb: 2}} variant={'h4'} component={'h4'}>Invitations</Typography>
        <Paper>
            <DataGrid
                columns={columns}
                rows={invitations}
                checkboxSelection
                autoHeight
                sx={{
                    border: 0,
                    '--DataGrid-overlayHeight': '300px',
                }}
                onRowSelectionModelChange={(newSelection) => {
                    setRowSelection(newSelection)
                    console.log(newSelection)
                }}
                rowSelectionModel={rowSelection}
                slots={{
                    toolbar: InvitationsToolbar,
                    noResultsOverlay: () => <NoResultsOverlay />,
                    noRowsOverlay: () => <NoRowsOverlay message={'No API keys'} />,
                }}
            />
        </Paper>

        <Dialog open={showModal} onClose={handleCloseModal} PaperProps={{sx: {width: 600}}}>
            <DialogTitle>Create a new invitation</DialogTitle>
            <DialogContent>
                <Stepper activeStep={activeTab}>
                    <Step>
                        <StepLabel>Create invitation</StepLabel>
                    </Step>
                    <Step>
                        <StepLabel>Send to user</StepLabel>
                    </Step>
                </Stepper>
            </DialogContent>
            {renderModalContent()}
        </Dialog>
    </>
}
