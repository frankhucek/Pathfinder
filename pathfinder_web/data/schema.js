import { makeExectuableScheme } from 'graphql-tools';
import resolvers from './resolvers';

const schema = `
  type Job {
    id: Int!
    images: [Image]!
    heatmap: Image
    blueprint: Image
    retail: Image
  }

  type Query {
    job(id: Int!): Job
  }

  type Mutation {
    createJob(
      id: Int
      images: [Image]!
    ): Job
    createHeatmap(
      id: Int
      heatmap: Image
    ): Job
    createBlueprint(
      id: Int
      blueprint: Image
    ): Job
    createRetailMap(
      id: Int
      retail: Image
    ): Job
  }

  schema {
    query: Query
    mutation: Mutation
  }
`;

const schema =  makeExectuableSchema({
    typeDefs: schema,
    resolvers
});
export { schema };
