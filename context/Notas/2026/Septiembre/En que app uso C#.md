En que app uso C# ?

Cuantos tipos de servicios hay?





# &#x09;Bienvenido a el comienzo donde construirás un sistema/diseño de software



### Que tipo de servicios/funcionalidades, quieres que tenga tu sistema o app



\- Buscar/administrar/registrar/Añadir, restar el INVENTARIO



\- habilidad para que te compren tus productos



\- Revisar orden pasada



\- checar reseñas de clientes



\-



\-



\-



## &#x09;			Designing the System



\- Do not overengenier, it is complex ( YAGNI)



\- Start with one plan to tackle at a time



Now we go with posible  Software Architecture Patterns that can feed the system



O´Riely E-Book



Layered

Event DRiven

MicroServices

Microkernel









SpaceBased



## &#x09;			Now we layer them like this



UI----------> Frontend(FE)



Lógica------> Backend(BE)



Data Base/Store/Storage





## &#x09;					TIPS



Use all types of Pattern´s



Achitecture Will Evolve



&#x20;- Requierments Will change



&#x20;- Some changes Will be expensive



&#x20;- Balance to Avoid over/under Engineering





## &#x09;				    Scalibility



### Vertical

Usalmente solo requiere mas Hardware y es para crecimiento linear



This means that it would need more hardware added Vertical Scaling(Scale UP) Make´s the nod´s more stronger



If you have one Server make it Stronger, Faster, by adding more Hardware, basically making optimizations on the software



### Horizontal

Debes darte cuenta rápido si un sistema ocupa escalar horizontalmente por que es poco usual



Horizontal Scaling Will need multiple server´s (Scaling OUT) This means spliting the load between Diffrent servers allowing you to have more scalability and Relibility



## &#x09;				    CAP theorem

&#x20;-State



&#x20;-no state



## &#x09;				   Log balancer

### &#x20;



### Strict Consistency

Whatever you say has to be AVAILABLE to everyone and all readers

### 

### Eventual Consistency

There´s a delay between when u write and when all readers con see that write



## &#x09;				   Data Sharing

We can have sharding or particinating basically we Split the data between 2 server´s.

By spliting you can scale each server Independetly (Flint Kafca)



There are multiple ways of Spliting the data:

For Example

Vertical Split by feature, or value    User base or do it by Hash





Sharding by Hash





User ID-------> Hash-------> Data base 1,2,3



You can also scale by using Consistent Hashing



Another thing we can do with data is Replicate where we can have multiple copies of the data in Diffrent server´s



Replicated data is very useful for Read-intensive



### &#x09;					Micro Services



is a way to design software as a suite of independently services usally around a buisness capeability you see: Usally You eill have a MONOLITH or a single application where you could have diffrent madules that do diffrent things



### &#x20;                                                  Notes

This is Important to have in a single system to control/modify/interact



Have this in the Original or Main Data Base same System to be able to share a comen data base between them



Modules interact with themselvels in-between but also store data to a comen database



Common Data Base= Itlearns or pases all its info like saving(even customers)



## &#x09;				    Saga Patterns



Orchastration



Asynchrounous

this one can send out avrios messages without waiting for a response



## &#x09;					Sumary



when you have a MONOLITH or asingle application you can cordinate between diffrent modules easily: they share the same database. You can put transactions in there



The Saga Pattern provides a form to communicate with 2 diffrent services in a "transaction like " you Will never get isolation but you can make it look like the ACID transactions that you had, when you only had one data base / service



ACID: atomic Consistent Isoltaed Durable



Orchastration: Works via Events



Chreoragraphy: uses event´s  by making services react to event´s and they would know, what to do or what not to do compensate



Note: Saga Patterns orchestrations Will have a Central service that Will take care of calling all the diffrent services in the right order or do compensations



Computer Science: there are only 2 main difficulties in this shit here boy! Cache invalidation and Naming things



Cache is something you can add later. It is more of a Optimization first we need to be sure of our Architecture



Event Driven Architecture



Maintainable then

Scalable then

Performat





event!----> Now this event could have some data sends to diffrent systems like for example: Inventory



Inventory: Will lower/increase upon purchasing/selling



This way the system intrested can subsribe (in this event) to it and execute the task that they need



plus for recommondation we wont need to sell the item as this Will allow the system to know who Recommended what item.

















Event Sourcing



Key Features

Complete Rebuild

Temporary Query -----> snapshot´s (evidence)

Event Replay------> OPtimization

Audit Log



Command Query Responsability segregation pattern

CQRS



Audit Log

Useful for when you want to see Reposetories usally in Git or GitHub



Parellel processing



CQRS split´s Read´s and the write you can also have additional



SERVICE DISCOVERY



SERVICE REGISTRY



DNS



Service Discovery Patterns



Serever-side Discovery



Client-side Discovery



Language



Java



Python



Node



3´rd party application use´s REGISTAR



container Orchestration Engine Kubernetes Virtual ip adress and VNS name



Side car



Note:

You can also use Client-side, Server-side Discovery to use the infrastructure to appropietly direct cals for you





Local Cache



Distribuated Cache (Reddis \& Memcoched)



&#x20;















&#x20;





&#x20;

