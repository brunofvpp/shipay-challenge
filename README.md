# Shipay Back-End Engineer Challenge


## Questão 1

Começaria a implementação pela responsabilidade central: validar se o endereço associado a um CNPJ coincide com o endereço retornado a partir de um CEP. É importante isolar as dependências externas e garantir que eventuais falhas nas APIs de terceiros não afetem a aplicação; por isso, a solução terá adapters específicos para cada provedor. Criaria um serviço orquestrador responsável por receber o CNPJ e o CEP, coordenar as chamadas externas e aplicar a regra de comparação. Esse orquestrador dependeria de interfaces abstratas, permitindo a troca ou evolução de provedores sem alterar a lógica principal. Para garantir resiliência, utilizaria uma estratégia de retentativas automáticas com backoff exponencial, como um Circuit Breaker evitando insistir em um serviço indisponível. Além disso, as chamadas teriam timeouts para garantir uma falha rápida e previsível, visto que a resposta deve ser síncrona. Após obter os dois resultados, os dados seriam normalizados antes da comparação, eliminando variações de abreviações, acentuação e formatação.

Segue diagramas C4 até o 3° nível:

<a href="question_1/C4_Context.png" target="_blank">C4 Context</a>

<a href="question_1/C4_Container.png" target="_blank">C4 Container</a>

<a href="question_1/C4_Component.png" target="_blank">C4 Component</a>


## Questão 2

A solução consiste em desacoplar a geração do relatório do fluxo de lançamento, garantindo que falhas no processo não impactem o fluxo principal. Implementaria uma arquitetura baseada em eventos assíncronos com armazenamento paralelo: o endpoint de lançamento permaneceria responsável pelo negócio principal e, após registrar o dado com sucesso, publicaria um evento contendo as informações necessárias. Para assegurar a consistência, utilizaria o padrão Transactional Outbox. Essa publicação deve ser não-bloqueante, utilizando um broker (como Kafka, RabbitMQ ou SNS/SQS). Para garantir a resiliência, seriam configuradas Dead Letter Queues (DLQs), permitindo que mensagens com falha no worker sejam enviadas para uma fila de erro para reprocessamento posterior, evitando a perda de dados. Por fim, o serviço de ingestão consumiria esses eventos e os gravaria em uma base paralela, otimizada para leituras agregadas e com esquemas desnormalizados. O processamento incluiria validação, enriquecimento e deduplicação idempotente, utilizando estratégias como Optimistic Lock para evitar contagens duplicadas.

Segue diagramas C4 até o 2° nível:

<a href="question_2/C4_Context.png" target="_blank">C4 Context</a>

<a href="question_2/C4_Container.png" target="_blank">C4 Container</a>


## Questão 3

Utilizaria o Locust para realizar os seguintes testes:

  - Teste de carga com spawn rate de 50 users/s até atingir 1.000 rps, visando determinar se o requisito de performance está sendo atendido.
  - Teste de estresse aumentando a carga gradualmente até encontrar o ponto de ruptura e determinar o limite de rps da aplicação.
  - Teste de estabilidade utilizando carga fixa de, no mínimo, 1.000 rps por um período prolongado para verificar se a aplicação se mantém estável, sem degradação de desempenho.

O ideal seria executar os testes em um ambiente o mais próximo possível do de produção. Com isso, será possível gerar relatórios contendo: gráficos de P99, taxa de erro e throughput para cada um dos cenários.


## Questão 4

  - Faltam testes.
  - Inconsistência na tipagem, apesar de não estar funcionando como strict, além de alguns contratos não estarem vinculados à classe abstrata, criando alto acoplamento.
  - Configuração fragmentada usando `Base` diferentes, abrindo brecha para cada parte usar metadatas diferentes.
  - `Controller` tem acoplamento implícito com estrutura de request e depende de path param inexistente.
  - `SqlRepository` e `RegistrationRepository` sofrem de fragmentação de sessão, apesar de funcionais, vão falhar silenciosamente, causando problema de DI e false UOW. Além do uso incorreto do selectinload.
  - `Orchestrator` está fazendo bypass na camada de domínio usando o repository.
  - `Tools` se tornou um God object com muitas responsabilidades além das queries feitas que estão propensas a sofrer SQL injection.
  - `ExceptionHandlerMiddleware` está expondo o stacktrace, revelando o funcionamento interno da aplicação, facilitando a engenharia reversa.


## Questão 5

[Implementação aqui](./question_5/README.md)


## Questão 6

  - Faltam testes.
  - O logger está com tamanho muito pequeno, é necessário aumentá-lo para diminuir a rotação de arquivos.
  - O config parser está apontando para o caminho errado, além de corrigir, seria interessante implementar um fallback para esse caso.
  - Muitos valores estão hardcoded, inclusive dados sensíveis. Sugiro criar env vars.
  - `add_job` irá falhar, pois espera receber um callable.
  - A query SQL tem o potencial de derrubar a aplicação por falta de memória se a tabela consultada for muito grande, sugiro deixar explícito na consulta somente os campos que serão utilizados e consumir os dados em chunks.
  - Caso dê erro de qualquer natureza, o arquivo xlsx que está sendo criado não será devidamente fechado, o melhor caminho seria adicionar um try/finally.
  - Evitaria expor dados sensíveis como senha, além de deixar os usuários vulneráveis à criação desse arquivo, o que pode violar as normas da LGPD.
  - Como os relatórios gerados não estão sendo excluídos, eventualmente a aplicação vai sofrer com falta de armazenamento. Se possível, crie usando `tempfile` ou envie-os para storage externo.
  - Algumas variáveis estão com nomes impróprios ou pouco descritivos.
  - Faz mais sentido utilizar o logger do que usar print.


## Questão 7

Eu utilizaria o padrão Adapter em conjunto com Strategy e, em cenários específicos, Factory. Dessa forma, cada serviço terá o seu próprio adapter, mantendo o código desacoplado e isolando a lógica de cada integração externa. Para facilitar a alternância de implementações em tempo de execução sem impactar a lógica de negócio, a Strategy aliada à Factory centralizaria a criação dos objetos, eliminando a necessidade de instanciar manualmente o adapter em diferentes partes do sistema.
