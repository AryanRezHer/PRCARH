const { createApp } = Vue

createApp({
  data(){
    return{
      like: null,
      recetid: null,
      newCom: '',
      message: 'Usuario con id: ',
      comentarios: []
    }
  },
  async mounted(){
      fetch('/getComentarios')
        .then(response => response.json())
        .then(data => {
          console.log(data)
          // Actualiza la interfaz de usuario con los datos recibidos
        this.comentarios = data;
        console.log(this.comentarios)
      })
        .catch(error => console.error('Error:', error));

      fetch('/get_likes')
        .then(response => response.json())
        .then(data => {
          this.like = data.likes
          this.recetid = data.receta_id
        })
        .catch(error => console.error('Error: ', error));
  },
  methods: {
    increment(){
      this.like++
      const id = this.recetid;
      fetch('/update_likes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ receta_id: id }),
    })
          .then(response => response.json())
          .then(data => {
              // Actualiza la interfaz de usuario con los datos recibidos
          console.log(data)
          })
          .catch(error => console.error('Error:', error));
  },
  decrement(){
      this.like--
      const id = this.recetid;
      fetch('/update_likes2', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ receta_id: id }),
    })
          .then(response => response.json())
          .then(data => {
              // Actualiza la interfaz de usuario con los datos recibidos
          console.log(data)
          })
          .catch(error => console.error('Error:', error));
  },
  nuevocomentario(){
    const nuevoComentario = this.newCom;
            fetch('/update_comentarios', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ comentario: nuevoComentario }),
            })
                .then(response => response.json())
                .then(data => {
                  console.log(this.comentarios)
                    // Actualiza la interfaz de usuario con los datos recibidos
                    this.comentarios.push(data);
                    this.newCom = '';
                })
                .catch(error => console.error('Error:', error));
  },
  eliminarcomentario(id){
            
    const borrarcomentario = id;
    fetch('/eliminarcomentario', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'id': borrarcomentario }),
    })
        .then(response => response.json())
        .then(data => {
            // Actualiza la interfaz de usuario con los datos recibidos
        this.comentarios = this.comentarios.filter((t) => t.id !== id)
        
        })
        .catch(error => console.error('Error:', error));
  }
},
  delimiters: ['{','}']
}).mount('#app')