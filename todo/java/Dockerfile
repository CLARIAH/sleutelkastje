FROM maven:3.9-eclipse-temurin-21 AS builder

WORKDIR /app

COPY ./src ./src
COPY ./pom.xml ./pom.xml

RUN mvn clean package

