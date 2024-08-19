FROM maven:3.9-eclipse-temurin-22-alpine AS builder

WORKDIR /app

COPY ./src ./src
COPY ./pom.xml ./pom.xml

RUN mvn clean package

#FROM openjdk:17-jdk-alpine
FROM eclipse-temurin:22
WORKDIR /
COPY --from=builder /app/target/todo-j-1.0-SNAPSHOT.jar /app.jar
CMD java -jar app.jar

EXPOSE 8000
