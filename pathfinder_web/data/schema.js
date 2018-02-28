import { makeExectuableScheme } from 'graphql-tools';

const schema = `
  type Query {
    hello: String
  }
`

export default makeExectuableSchema({}
    typeDefs: schema,
});
