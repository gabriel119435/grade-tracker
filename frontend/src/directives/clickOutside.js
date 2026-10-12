// intended behavior: closes floating ui (dropdown list) when the user clicks anywhere else on the page
// the handler closes the ui (AppDropdown.vue sets open to false), called by the listener on a click outside

// map has structure tag-element:handler-function
// the handler is the v-click-outside value in the template
const handlers = new Map()

// not part of the directive: plain browser code, runs once on import, reads the map the directive fills
// adds a behavior to the top node: on any click, each map tag element runs its handler if the click was outside it
document.addEventListener('click', (e) => {
    handlers.forEach((handler, domElement) => {
        if (!domElement.contains(e.target)) handler()
    })
})

// mounted/updated/unmounted run on tags with v-click-outside to add, refresh and remove their map entry
export const clickOutside = {
    mounted(domElement, binding) {
        handlers.set(domElement, binding.value)
    },
    updated(domElement, binding) {
        handlers.set(domElement, binding.value)
    },
    unmounted(domElement) {
        handlers.delete(domElement)
    },
}
