FROM maven:3.9-eclipse-temurin-21-alpine AS builder

WORKDIR /app

COPY ./src ./src
COPY ./pom.xml ./pom.xml

RUN mvn clean package

FROM openjdk:21-jdk-alpine
WORKDIR /
COPY --from=builder /app/target/*.jar /app.jar
CMD java -jar app.jar

