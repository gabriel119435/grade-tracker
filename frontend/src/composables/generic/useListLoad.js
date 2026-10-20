import {useLoad} from './useLoad.js'

// fetchFn: api function returning a list or {error}, ex: getStudents
export function useListLoad(fetchFn) {
    // items: last loaded list: [{id: 1, username: 'alice', grade_count: 12}]
    const {data: items, failed, load} = useLoad(fetchFn, [])

    // list state shared by the teachers, students, categories and teacher grades views
    // load() fetches and stores, see useLoad.js
    // read items and failed, write via load()
    return {items, failed, load}
}
