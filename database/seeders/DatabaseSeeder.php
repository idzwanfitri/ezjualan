<?php

namespace Database\Seeders;

use App\Models\Coupon;
use App\Models\Customer;
use App\Models\Order;
use App\Models\Product;
use App\Models\User;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        User::query()->firstOrCreate(
            ['email' => 'staff@ezjualan.test'],
            ['name' => 'Staff User', 'password' => bcrypt('password')],
        );

        $products = Product::factory(20)->create();

        Coupon::factory()->percentage(10)->create(['code' => 'DISKAUN10']);
        Coupon::factory()->fixed(20)->create(['code' => 'JIMAT20']);
        Coupon::factory()->expired()->create(['code' => 'TAMAT2025']);
        Coupon::factory()->inactive()->create(['code' => 'TIDAKAKTIF']);

        $customers = Customer::factory(15)->create();

        for ($i = 0; $i < 50; $i++) {
            $product = $products->random();
            $quantity = fake()->numberBetween(1, 5);

            Order::factory()->create([
                'customer_id' => $customers->random()->id,
                'product_id' => $product->id,
                'product_name' => $product->name,
                'unit_price' => $product->price,
                'quantity' => $quantity,
                'total_price' => $product->price * $quantity,
            ]);
        }
    }
}
