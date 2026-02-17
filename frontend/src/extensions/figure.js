import { Node, mergeAttributes } from '@tiptap/core'

export const Figure = Node.create({
  name: 'figure',
  group: 'block',
  content: 'inline*',
  draggable: true,
  isolating: true,

  addAttributes() {
    return {
      src: { default: null },
      alt: { default: '' },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'figure',
        contentElement: 'figcaption',
        getAttrs(node) {
          const img = node.querySelector('img')
          if (!img) return false
          return {
            src: img.getAttribute('src'),
            alt: img.getAttribute('alt') || '',
          }
        },
      },
    ]
  },

  renderHTML({ node, HTMLAttributes }) {
    return [
      'figure',
      mergeAttributes(HTMLAttributes),
      [
        'img',
        {
          src: node.attrs.src,
          alt: node.attrs.alt,
          draggable: false,
        },
      ],
      ['figcaption', 0],
    ]
  },

  addCommands() {
    return {
      insertFigure:
        (attrs) =>
        ({ chain }) => {
          return chain()
            .insertContent({
              type: this.name,
              attrs: { src: attrs.src, alt: attrs.alt || '' },
              content: [
                {
                  type: 'text',
                  text: attrs.caption || '輸入圖說...',
                },
              ],
            })
            .run()
        },
    }
  },
})

export default Figure
