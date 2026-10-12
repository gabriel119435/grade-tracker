export function useLatestCall() {
    let latest = 0

    function start() {
        const current = ++latest
        return () => current === latest
    }

    // switching student, date or limit fast can make a newer request be answered before an older one
    // the older answer, arriving last, overwrites the newer data: new student shows the old student's grades
    // start() at the beginning of each call returns isLatest(), true only while no newer call started
    // ex: const isLatest = start(), then after await: if (!isLatest()) return
    return {start}
}
