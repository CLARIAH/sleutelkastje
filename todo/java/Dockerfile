FROM maven:3.9-eclipse-temurin-21 AS builder

WORKDIR /app

COPY ./src ./src
COPY ./pom.xml ./pom.xml

RUN mvn clean package

FROM openjdk:11
WORKDIR /
COPY --from=builder /app/target/*.jar /app.jar
CMD java -jar app.jar

