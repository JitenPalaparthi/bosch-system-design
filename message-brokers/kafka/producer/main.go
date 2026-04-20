package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"strconv"
	"time"

	"github.com/twmb/franz-go/pkg/kgo"
)

var (
	Topic         string
	ConsumerGroup string
)

func main() {

	flag.StringVar(&Topic, "topic", "orders", "--topic=omnenext.demo.v1")
	flag.StringVar(&ConsumerGroup, "cg", "demo-consumer-group", "--cg=demo-consumer-group")
	flag.Parse()

	seeds := []string{"localhost:9092"}
	// One client can both produce and consume!
	// Consuming can either be direct (no consumer group), or through a group. Below, we use a group.
	cl, err := kgo.NewClient(
		kgo.SeedBrokers(seeds...),
		// kgo.ConsumerGroup(ConsumerGroup),
		// kgo.ConsumeTopics(Topic),
		kgo.RequiredAcks(kgo.AllISRAcks()), // or kgo.RequireOneAck(), kgo.RequireNoAck()
		//kgo.DisableIdempotentWrite()

	)
	if err != nil {
		panic(err)
	}
	defer cl.Close()

	ctx := context.Background()

	// 1.) Producing a message
	// All record production goes through Produce, and the callback can be used
	// to allow for synchronous or asynchronous production.

	//users := GenUserData()
	time.Sleep(time.Second * 5)
	for i := 1; ; i++ {

		time.Sleep(time.Millisecond * 300)
		user1 := User{
			ID:    uint(i + 1),
			Name:  " User " + strconv.Itoa(i+1),
			Email: fmt.Sprintf("user%d@example.com", i+1),
		}
		//rnd := rand.IntN(3)
		record := &kgo.Record{Topic: Topic, Value: user1.ToBytes(), Key: nil}
		cl.Produce(ctx, record, func(r *kgo.Record, err error) {
			//defer wg.Done()
			if err != nil {
				fmt.Printf("record had a produce error: %v\n", err)
			}
			user := new(User)
			json.Unmarshal(r.Value, user)
			//fmt.Println(user)
			fmt.Println("Producer-->", r.ProducerID, "Topid-->", r.Topic, "Partition:", r.Partition, "Offset:", r.Offset, "Value:", user)

		})

		// Alternatively, ProduceSync exists to synchronously produce a batch of records.
		if err := cl.ProduceSync(ctx, record).FirstErr(); err != nil {
			fmt.Printf("record had a produce error while synchronously producing: %v\n", err)
		}
	}

	cl.Flush(ctx)
	log.Println("done")

}

type User struct {
	ID    uint   `json:"id"`
	Name  string `json:"name"`
	Email string `json:"email"`
}

func (u *User) ToBytes() []byte {
	bytes, _ := json.Marshal(u)
	return bytes
}

func GenUserData() []User {
	users := make([]User, 100) // preallocate slice

	for i := 0; i < 100; i++ {
		users[i] = User{
			ID:    uint(i + 1),
			Name:  " User " + strconv.Itoa(i+1),
			Email: fmt.Sprintf("user%d@example.com", i+1),
		}
	}
	return users
}
