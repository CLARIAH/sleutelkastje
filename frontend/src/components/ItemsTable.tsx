import {IItem} from "../routes/appManagement/applicationItems.tsx";
import {DataGrid, GridColDef, GridRowSelectionModel, GridToolbarContainer} from "@mui/x-data-grid";
import {
    Box,
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle, FormControl, Input, InputLabel,
    Paper,
    Typography
} from "@mui/material";
import {NoResultsOverlay} from "./NoResultsOverlay.tsx";
import {NoRowsOverlay} from "./NoRowsOverlay.tsx";
import {useState} from "react";
import {AddRounded, DeleteRounded} from "@mui/icons-material";
import {ConfirmDialog} from "./ConfirmDialog.tsx";
import axios from "axios";
import {useRevalidator} from "react-router-dom";
import {IApp} from "../routes/root.tsx";

const columns: GridColDef[] = [
    {field: 'id', headerName: 'ID', width: 70},
    {field: 'name', headerName: 'Name', width: 200},
]

export function ItemsTable({app, items}: {app: IApp, items: IItem[]}) {
    const [rowSelection, setRowSelection] = useState<GridRowSelectionModel>([])
    const [showModal, setShowModal] = useState<boolean>(false)
    const [showDeleteDialog, setShowDeleteDialog] = useState<boolean>(false)
    const [itemName, setItemName] = useState<string>('')

    const revalidator = useRevalidator()

    function closeDeleteDialog() {
        setShowDeleteDialog(false)
    }

    function deleteItems() {
        console.log("Deleting:", rowSelection)
        closeDeleteDialog()
        revalidator.revalidate()
    }

    function createItem(e: { preventDefault: () => void; }) {
        e.preventDefault()
        axios.post('/api/apps/' + app.mnemonic + '/items', {
            name: itemName
        }).then(response => {
            console.log(response)
            handleCloseModal()
            revalidator.revalidate()
        })
    }

    function ItemsToolbar() {
        return (
            <GridToolbarContainer>
                <Button onClick={() => setShowModal(true)} startIcon={<AddRounded />} >Create item</Button>
                <Box sx={{flexGrow: 1}} />
                <Button onClick={() => {setShowDeleteDialog(true)}} color={'error'} startIcon={<DeleteRounded />} disabled={rowSelection.length == 0} >Delete</Button>
                <ConfirmDialog open={showDeleteDialog} onClose={closeDeleteDialog} onConfirm={deleteItems} title={"Delete items keys?"} message={"Are you sure you want to delete these items? Users will lose their access to these items as well."} />
            </GridToolbarContainer>
        )
    }

    function handleCloseModal() {
        setShowModal(false)
        setItemName('')
    }

    return <>
        <Typography sx={{mb: 2}} variant={'h4'} component={'h4'}>Items</Typography>
        <Paper>
            <DataGrid
                columns={columns}
                rows={items}
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
                    toolbar: ItemsToolbar,
                    noResultsOverlay: () => <NoResultsOverlay />,
                    noRowsOverlay: () => <NoRowsOverlay message={'No items'} />,
                }}
            />
        </Paper>

        <Dialog open={showModal} onClose={handleCloseModal} PaperProps={{
            sx: {width: 600}
        }}>
            <Box component={'form'} onSubmit={createItem}>
                <DialogTitle>Create an Item</DialogTitle>
                <DialogContent>
                    <DialogContentText sx={{mb: 2}}>Create a new item.</DialogContentText>
                    <FormControl fullWidth>
                        <InputLabel htmlFor={"item-name"}>Name</InputLabel>
                        <Input id={'item-name'} type={'text'} value={itemName} onChange={(e) => setItemName(e.target.value)} />
                    </FormControl>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseModal}>Cancel</Button>
                    <Button type={'submit'}>Create</Button>
                </DialogActions>
            </Box>
        </Dialog>
    </>
}
