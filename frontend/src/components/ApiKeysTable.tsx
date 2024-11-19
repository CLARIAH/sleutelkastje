import {DataGrid, GridColDef, GridRowId, GridRowSelectionModel, GridToolbarContainer} from "@mui/x-data-grid";
import {
    Autocomplete,
    Box,
    Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle,
    FormControl, IconButton, Input, InputAdornment,
    InputLabel,
    Paper,
    Step,
    StepLabel,
    Stepper,
    TextField,
    Typography
} from "@mui/material";
import {IApiKey} from "../routes/user/apiKeys.tsx";
import {NoResultsOverlay} from "./NoResultsOverlay.tsx";
import {NoRowsOverlay} from "./NoRowsOverlay.tsx";
import {useState} from "react";
import {AddRounded, ContentCopyRounded, DeleteRounded} from "@mui/icons-material";
import axios from "axios";
import moment from 'moment'
import {useRevalidator} from "react-router-dom";
import {ConfirmDialog} from "./ConfirmDialog.tsx";
import {IApp} from "../routes/root.tsx";

const columns: GridColDef[] = [
    {field: 'name', headerName: 'Name', width: 200},
    {field: 'application', headerName: 'Application', width: 200},
    {
        field: 'key',
        headerName: 'Key',
        width: 260,
        valueGetter: (_value, row) => row.readable_part + '*****',
        renderCell: params => {
            return <span style={{
                fontFamily: "Victor Mono",
                fontWeight: "100"
            }}>{params.value}</span>
        }
    },
    {
        field: 'last_used',
        headerName: 'Last used',
        width: 200,
        valueGetter: (value) => value == null ? 'Never' : moment(value).fromNow()
    },
]

const modalStyle = {
    width: 600,
}

export function ApiKeysTable({keys, apps}: {keys: IApiKey[], apps: IApp[]}) {
    const [showModal, setShowModal] = useState<boolean>(false);
    const [rowSelection, setRowSelection] = useState<GridRowSelectionModel>([])
    const [activeTab, setActiveTab] = useState(0)
    const [keyName, setKeyName] = useState<string>('')
    const [displayKey, setDisplayKey] = useState<string>('')
    const [showDeleteDialog, setShowDeleteDialog] = useState(false)
    const [selectedApp, setSelectedApp] = useState<IApp | null>(null)
    const revalidator = useRevalidator()

    const appsList: IApp[] = [{name: 'Sleutelkastje', mnemonic: '', current_role: ''}, ...apps]


    function deleteKeys() {
        const prefixes = rowSelection.map((withHuc: GridRowId) => {
            return (withHuc as string).substring('huc:'.length)
        })

        axios.delete('/api/keys', {
            data: {
                'prefixes': prefixes
            }
        }).then(response => {
            console.log(response.data)
            closeDeleteDialog()
            revalidator.revalidate()
        })
    }

    function closeDeleteDialog() {
        setShowDeleteDialog(false)
    }

    function createKey(e: { preventDefault: () => void; }) {
        e.preventDefault()

        let postData: {name: string, appMnemonic?: string} = {
            name: keyName
        }
        if (selectedApp != null) {
            postData.appMnemonic = selectedApp.mnemonic
        }

        axios.post('/api/keys', postData).then(response => {
            console.log(response)
            setDisplayKey(response.data.key)
            setActiveTab(1)
            setSelectedApp(null)
            revalidator.revalidate()
        })
    }

    function handleCloseModal() {
        setActiveTab(0)
        setShowModal(false)
        setKeyName('')
        setDisplayKey('')
    }

    function renderModalContent() {
        switch (activeTab) {
            case 0:
                return <Box component={"form"} onSubmit={createKey} noValidate>
                    <DialogContent>
                        <DialogContentText>
                            Please pick a name for your new key so you can recognize it.
                        </DialogContentText>
                        <Box sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            width: '100%',
                            gap: 2
                        }}>
                            <TextField id={"invitationRole"} value={keyName} onChange={e => setKeyName(e.target.value)} label={"Name"} variant={"standard"} />
                            <Autocomplete
                                renderInput={(params) => (
                                    <TextField {...params} label={'App'} variant={'standard'} />
                                )}
                                getOptionLabel={(option) => option.name}
                                options={appsList}
                                value={selectedApp}
                                onChange={(_e, newValue) => setSelectedApp(newValue)}
                                />
                        </Box>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleCloseModal}>Cancel</Button>
                        <Button type={'submit'}>Create</Button>
                    </DialogActions>
                </Box>

            case 1:
                return <>
                    <DialogContent>
                        <DialogContentText sx={{mb: 2}}>
                            API Key Generated
                        </DialogContentText>
                        <DialogContentText sx={{mb: 2}}>
                            Please store your API key somewhere safe before closing this window. You
                            can only view the key once, so once you close the window you cannot see it
                            anymore.
                        </DialogContentText>
                        <FormControl fullWidth sx={{m: 1}}>
                            <InputLabel htmlFor="api-key">API Key</InputLabel>
                            <Input
                                id={'api-key'}
                                type={'text'}
                                value={displayKey}
                                disabled
                                endAdornment={
                                    <InputAdornment position={'end'}>
                                        <IconButton onClick={() => {navigator.clipboard.writeText(displayKey)}} aria-label={"Copy to clipboard"}>
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

    function ApiKeysToolbar() {
        return (
            <GridToolbarContainer>
                <Button onClick={() => setShowModal(true)} startIcon={<AddRounded />} >Create API key</Button>
                <Box sx={{flexGrow: 1}} />
                <Button onClick={() => {setShowDeleteDialog(true)}} color={'error'} startIcon={<DeleteRounded />} disabled={rowSelection.length == 0} >Delete</Button>
                <ConfirmDialog open={showDeleteDialog} onClose={closeDeleteDialog} onConfirm={deleteKeys} title={"Delete API keys?"} message={"Are you sure you want to delete these API keys? Once deleted you cannot use them anymore."} />
            </GridToolbarContainer>
        )
    }


    return <>
        <Typography sx={{mb: 2}} variant={'h4'} component={'h4'}>Keys</Typography>
        <Paper>
            <DataGrid
                columns={columns}
                rows={keys}
                checkboxSelection
                autoHeight
                getRowId={(data) => data.readable_part}
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
                    toolbar: ApiKeysToolbar,
                    noResultsOverlay: () => <NoResultsOverlay />,
                    noRowsOverlay: () => <NoRowsOverlay message={'No API keys'} />,
                }}
            />
        </Paper>

        <Dialog open={showModal} onClose={handleCloseModal} PaperProps={{
            sx: modalStyle,
        }}>
            <DialogTitle>Create an API key</DialogTitle>
            <DialogContent>
                <Stepper activeStep={activeTab}>
                    <Step>
                        <StepLabel>Create API key</StepLabel>
                    </Step>
                    <Step>
                        <StepLabel>Save key</StepLabel>
                    </Step>
                </Stepper>
            </DialogContent>
            {renderModalContent()}
        </Dialog>
    </>
}
