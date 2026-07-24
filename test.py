from langchain_core.messages import HumanMessage
from agent.graph import agente_topo

def probar_agente():
    print("="*50)
    print("🤖 BIENVENIDO AL ENTORNO DE PRUEBAS - AGENTE TOPO 🤖")
    print("Escribe 'salir' para terminar la prueba.")
    print("="*50)
    
    # ---------------------------------------------------------
    # ⚙️ CONFIGURACIÓN DE LA PRUEBA
    # Cambia estos valores para probar diferentes escenarios
    # Roles válidos: "cliente", "empleado", "administrador"
    # ---------------------------------------------------------
    rol_prueba = "administrador" 
    folio_prueba = "" # Simula que el usuario inició sesión con este folio
    
    print(f"Configuración actual -> Rol: [{rol_prueba}] | Folio: [{folio_prueba}]\n")

    while True:
        pregunta = input("👤 Tú (Pregunta): ")
        
        if pregunta.lower() in ['salir', 'exit', 'quit']:
            print("👋 Saliendo del entorno de pruebas...")
            break
        
        if not pregunta.strip():
            continue

        # Construimos el estado inicial tal como lo enviaría Streamlit
        estado_inicial = {
            "messages": [HumanMessage(content=pregunta)],
            "user_role": rol_prueba,
            "user_folio": folio_prueba
        }
        
        print("\n⚙️ Procesando solicitud... (revisa los prints de los nodos)\n")
        
        try:
            # Ejecutamos el grafo
            resultado = agente_topo.invoke(estado_inicial)
            
            # Extraemos la respuesta final generada por el agente
            respuesta_final = resultado["messages"][-1].content
            
            print("-" * 50)
            print(f"🤖 AGENTE TOPO:\n{respuesta_final}")
            print("-" * 50)
            
            # --- DEBUG INFO ---
            # Esto te ayudará a ver qué hizo el agente "por debajo"
            print(f"🛠️  [DEBUG INFO]")
            print(f"  - Acción Final / Estado: {resultado.get('accion_final', 'N/A')}")
            
            if resultado.get("grafico_generado"):
                print(f"  - 📊 Gráfico generado: {resultado.get('grafico_generado')}")
            
            if resultado.get("folio"):
                print(f"  - 📌 Folio detectado: {resultado.get('folio')}")
                
            print("\n")
            
        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO DURANTE LA EJECUCIÓN: {e}\n")

if __name__ == "__main__":
    probar_agente()