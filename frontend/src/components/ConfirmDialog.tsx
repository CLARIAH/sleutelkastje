import {Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle} from "@mui/material";

export function ConfirmDialog({title, message, onConfirm, onClose, open}: {title: string, message: string, onConfirm: () => void, onClose: () => void, open: boolean}) {
    return <Dialog open={open} onClose={onClose} aria-label={title} aria-description={message}>
        <DialogTitle id="alert-dialog-title">
            {title}
        </DialogTitle>
        <DialogContent>
            <DialogContentText id="alert-dialog-description">
                {message}
            </DialogContentText>
        </DialogContent>
        <DialogActions>
            <Button onClick={onClose}>Cancel</Button>
            <Button color={'error'} onClick={onConfirm} autoFocus>
                Confirm
            </Button>
        </DialogActions>
    </Dialog>
}
