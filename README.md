# Shipay Back-End Engineer Challenge


## Questão 1

Comecaria a implementação pela responsabilidade central: validar se o endereço associado a um CNPJ coincide com o endereço retornado a partir de um CEP. É importante isolar as dependências externas e garantir que eventuais falhas nas APIs de terceiros não afetem a aplicação. Por isso, a solução terá adapters específicos para cada provedor. Eu criaria um serviço orquestrador responsável por receber o CNPJ e o CEP, coordenar as chamadas externas e aplicar a regra de comparação. Esse orquestrador dependeria de interfaces abstratas, podendo realizar troca ou evoluções de provedores sem alterar a lógica principal. Para garantir resiliência, eu utilizaria uma estratégia de retentativas automáticas com backoff exponencial, como um Circuit Breaker simplificado, evitando insistir em um serviço indisponível e reduzindo o tempo total de resposta, bem como as chamadas teriam timeouts para retornar uma falha rápida e previsível ao inves de aguardar indefinidamente, já que a resposta precisa ser síncrona. Após obter os dois resultados, eu normalizaria os dados antes da comparação para evitar variações de abreviações, acentuação e formatação.

Segue diagramas C4 até o 3 nível:

<a href="question_1/C4_Context.png" target="_blank">C4 Context</a>

<a href="question_1/C4_Container.png" target="_blank">C4 Container</a>

<a href="question_1/C4_Component.png" target="_blank">C4 Component</a>


## Questão 2

A solução é desacoplar a geração do relatório do fluxo de lançamento, fazendo com que falhas no novo processo não impacte o fluxo principal. Eu implementaria uma arquitetura baseada em eventos assíncronos com armazenamento paralelo. O endpoint de lançamento continua responsável pelo negócio principal, após registrar com sucesso o dado, ele publica um evento contendo os dados necessários para o relatório mas também utiliza transactional outbox para controle dos eventos emitidos. Essa publicação não deve ser bloqueante. Utilizaria um broker como Kafka, RabbitMQ ou SNS/SQS para receber eventos junto com a criação de dead letter queues para garantir que nenhum dado de relatório seja perdido em falhas críticas, as mensagens que falharem no worker podem ser enviadas para uma fila de erro para reprocessamento posterior. Criaria o serviço de ingestão do relatório que tem um worker que consome os eventos e grava em uma base paralela, desenhada para leitura agregada. Essa base até pode ter schemas desnormalizados por relatório para facilitar as consultas. O processamento inclui validação, enriquecimento e deduplicação idempotente para evitar contagens duplicadas como optimistic lock.

Segue diagramas C4 até o 2 nível:

<a href="question_2/C4_Context.png" target="_blank">C4 Context</a>

<a href="question_2/C4_Container.png" target="_blank">C4 Container</a>


## Questão 3

Eu usaria o Locust para realizar os seguintes testes:

  - Teste de carga com spawn rate de 50 users/s até atingir 1.000 rp/s para determinar se o requisito de performace está sendo atendido.
  - Teste de stress aumentando a carga gradualmente até encontrar o ponto de ruptura e determinar o limite de rp/s da aplicação.
  - Teste de estabilidade utilizando carga fixa de pelo menos 1000 rp/s por um periodo maior para determinar se a aplicação se mantem estavel sem degradar a performace.

O ideal seria rodar os testes em um ambiente o mais proximo possivel de produção. Com isso é possivel gerar os relatórios com: gráfico de P99, taxa de erro, throughput para cada um dos testes
