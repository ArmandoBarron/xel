function MessageStack() {
    this.messages = []; // Array para almacenar los mensajes
  
    // Método para agregar un mensaje a la pila
    this.push = function(message) {
      if (this.messages.length >= 15) {
        this.messages.shift(); // Eliminar el mensaje más antiguo
      }

      this.messages.push(message); // Agregar el nuevo mensaje al final de la pila
    };
  
    // Método para obtener todos los mensajes de la pila
    this.getMessages = function() {
      return this.messages;
    };
  
    // Método para vaciar la pila de mensajes
    this.clear = function() {
      this.messages = [];
    };
  }
  
function LogerStack(id_front){
    this.stack = MessageStack()
    this.front = $("#"+id_front)

    this.CreateNotification = function(mensaje,tipo="") {
        // Crear el elemento div para la notificación
        icono='<i class="icon fas fa-bug"></i>'
        if (tipo=="danger"){
            icono = '<i class="icon fas fa-times"></i>'
        }
        else if (tipo=="warning"){
            icono = '<i class="icon fas fa-exclamation-triangle"></i>'
        }
        else if (tipo=="success"){
            icono = '<i class="icon fas fa-check-circle"></i>'
        }
        else if (tipo=="info"){
            icono = '<i class="icon fas fa-info"></i>'
        }
        var notificacion = $(`<li><span class="line"></span> ${icono} ${mensaje} </li>`);
        // Establecer las clases CSS según el tipo de notificación
        //notificacion.addClass('alert');
        //notificacion.addClass(`alert-${tipo}`);

        return notificacion
    
      }

    this.push = function(message,type_message) {
        var today = new Date();
        time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds() + " - ";
  
        var notificacion = this.CreateNotification(time+message,type_message)
        if (this.front.children().length >= 15) {
            this.front.children().last().remove(); // Eliminar el div más antiguo
          }

          this.front.prepend(notificacion);
      };
    

}

  // Uso de la función MessageStack
  //var stack = new MessageStack();
  
  //stack.push("Mensaje 1");
  //stack.push("Mensaje 2");
  //stack.push("Mensaje 3");
  
  //var messages = stack.getMessages();
  //console.log(messages); // Resultado: ["Mensaje 1", "Mensaje 2", "Mensaje 3"]
  
  //stack.push("Mensaje 4");
  //messages = stack.getMessages();
  //console.log(messages); // Resultado: ["Mensaje 2", "Mensaje 3", "Mensaje 4"]
  
  //stack.clear();
  
  //messages = stack.getMessages();
  //console.log(messages); // Resultado: []