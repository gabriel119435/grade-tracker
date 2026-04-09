const handlers = new Map()

document.addEventListener('click', (e) => {
    handlers.forEach((handler, domElement) => {
        // calls handler if click is outside domElement
        if (!domElement.contains(e.target)) handler()
    })
})

export const clickOutside = {
    // domElement is the actual dom element like document.querySelector('.app-dropdown')
    // binding.value is a function like () => open = false
    mounted(domElement, binding) {
        handlers.set(domElement, binding.value)
    },
    updated(domElement, binding) { // vue calls this when element is re-rendered
        handlers.set(domElement, binding.value)
    },
    unmounted(domElement) { // vue calls this when element is removed from dom
        handlers.delete(domElement)
    },
}
