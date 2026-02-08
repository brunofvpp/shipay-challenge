# Shipay Back-End Engineer Challenge


## Questão 1

Comecaria a implementação pela responsabilidade central: validar se o endereço associado a um CNPJ coincide com o endereço retornado a partir de um CEP. É importante isolar as dependências externas e garantir que eventuais falhas nas APIs de terceiros não afetem a aplicação. Por isso, a solução terá adapters específicos para cada provedor. Eu criaria um serviço orquestrador responsável por receber o CNPJ e o CEP, coordenar as chamadas externas e aplicar a regra de comparação. Esse orquestrador dependeria de interfaces abstratas, podendo realizar troca ou evoluções de provedores sem alterar a lógica principal. Para garantir resiliência, eu utilizaria uma estratégia de retentativas automáticas com backoff exponencial, como um Circuit Breaker simplificado, evitando insistir em um serviço indisponível e reduzindo o tempo total de resposta, bem como as chamadas teriam timeouts para retornar uma falha rápida e previsível ao inves de aguardar indefinidamente, já que a resposta precisa ser síncrona. Após obter os dois resultados, eu normalizaria os dados antes da comparação para evitar variações de abreviações, acentuação e formatação.

Segue diagramas C4 até o 3 nível:

<a href="question_1/C4_Context.png" target="_blank">C4 Context</a>

<a href="question_1/C4_Container.png" target="_blank">C4 Container</a>

<a href="question_1/C4_Component.png" target="_blank">C4 Component</a>
