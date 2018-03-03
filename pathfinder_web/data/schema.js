import { makeExectuableScheme } from 'graphql-tools';

const schema = `
  type Query {
    job(id: Int!): Job
  }

  type Mutation {
    createJob(images: [Image]!): Job
  }

  type Job {
    id: Int!
    images: [Image]!
    heatmap: Image
    blueprint: Image
    retail: Image
  }
`

export default makeExectuableSchema({}
    typeDefs: schema,
});
