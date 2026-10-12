import {useToast} from './useToast.js'
import {translateError} from '../../utils/translateError.js'

// withLoading: from the caller's useLoading(), keeps one action at a time per page
export function useAction(withLoading) {
    const {toast} = useToast()

    async function runAction(apiCall, onSuccess) {
        await withLoading(async () => {
            const data = await apiCall()
            if (data.error) {
                toast(translateError(data.error), 'error')
                return
            }
            await onSuccess(data)
        })
    }

    // button actions shared by the categories, users, teachers, grades and top bar handlers
    // runAction(apiCall, onSuccess) runs apiCall inside withLoading
    // an error becomes a toast, otherwise onSuccess(data) runs, ex: clear the input and reload the list
    return {runAction}
}
